import os
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class MovieLensCFTrainer:
    def __init__(self, data_dir=None):
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "datasets", "movielens", "ml-latest-small")

        self.data_dir = data_dir
        self.movies_path = os.path.join(data_dir, "movies.csv")
        self.ratings_path = os.path.join(data_dir, "ratings.csv")

        self.movies_df = None
        self.ratings_df = None

        self.train_df = None
        self.test_df = None

        self.user_movie_matrix = None
        self.user_similarity = None
        self.item_similarity = None

    def load_data(self):
        if not os.path.exists(self.movies_path):
            raise FileNotFoundError(f"找不到 movies.csv: {self.movies_path}")
        if not os.path.exists(self.ratings_path):
            raise FileNotFoundError(f"找不到 ratings.csv: {self.ratings_path}")

        self.movies_df = pd.read_csv(self.movies_path)
        self.ratings_df = pd.read_csv(self.ratings_path)

        print("数据加载成功")
        print(f"电影数: {len(self.movies_df)}")
        print(f"评分数: {len(self.ratings_df)}")
        print(f"用户数: {self.ratings_df['userId'].nunique()}")

    def preprocess_data(self, min_user_ratings=5):
        """
        只保留评分次数不少于 min_user_ratings 的用户
        """
        user_counts = self.ratings_df["userId"].value_counts()
        valid_users = user_counts[user_counts >= min_user_ratings].index

        self.ratings_df = self.ratings_df[self.ratings_df["userId"].isin(valid_users)].copy()

        print("\n预处理完成")
        print(f"保留用户数: {self.ratings_df['userId'].nunique()}")
        print(f"保留评分数: {len(self.ratings_df)}")

    def train_test_split_leave_one_out(self):
        """
        对每个用户，按时间排序，最后一条评分作为测试集，其余作为训练集
        """
        ratings_sorted = self.ratings_df.sort_values(["userId", "timestamp"])
        test_rows = ratings_sorted.groupby("userId").tail(1)
        train_rows = ratings_sorted.drop(test_rows.index)

        self.train_df = train_rows.copy()
        self.test_df = test_rows.copy()

        print("\n训练测试集划分完成")
        print(f"训练集评分数: {len(self.train_df)}")
        print(f"测试集评分数: {len(self.test_df)}")

    def build_matrix(self):
        """
        构建用户-电影评分矩阵
        """
        self.user_movie_matrix = self.train_df.pivot_table(
            index="userId",
            columns="movieId",
            values="rating",
            fill_value=0
        )

        print("\n评分矩阵构建完成")
        print(f"矩阵形状: {self.user_movie_matrix.shape}")

    def calculate_similarity(self):
        """
        计算用户相似度和物品相似度
        """
        user_matrix_values = self.user_movie_matrix.values

        self.user_similarity = cosine_similarity(user_matrix_values)
        self.item_similarity = cosine_similarity(user_matrix_values.T)

        print("\n相似度计算完成")
        print(f"用户相似度矩阵: {self.user_similarity.shape}")
        print(f"物品相似度矩阵: {self.item_similarity.shape}")

    def recommend_user_based(self, user_id, top_k=10):
        if user_id not in self.user_movie_matrix.index:
            return []

        user_index = self.user_movie_matrix.index.get_loc(user_id)
        similarities = self.user_similarity[user_index]

        user_ratings = self.user_movie_matrix.iloc[user_index]
        unrated_movies = user_ratings[user_ratings == 0].index

        predicted_scores = []

        for movie_id in unrated_movies:
            movie_ratings = self.user_movie_matrix[movie_id]
            rated_users_mask = movie_ratings > 0

            if rated_users_mask.sum() == 0:
                continue

            sim_scores = similarities[rated_users_mask.values]
            rating_scores = movie_ratings[rated_users_mask].values

            denom = np.sum(np.abs(sim_scores))
            if denom > 0:
                predicted_rating = np.sum(sim_scores * rating_scores) / denom
                predicted_scores.append((movie_id, predicted_rating))

        predicted_scores.sort(key=lambda x: x[1], reverse=True)
        return predicted_scores[:top_k]

    def recommend_item_based(self, user_id, top_k=10):
        if user_id not in self.user_movie_matrix.index:
            return []

        user_row = self.user_movie_matrix.loc[user_id]
        rated_movies = user_row[user_row > 0].index.tolist()
        unrated_movies = user_row[user_row == 0].index.tolist()

        if len(rated_movies) == 0:
            return []

        movie_index_map = {movie_id: idx for idx, movie_id in enumerate(self.user_movie_matrix.columns)}

        predicted_scores = []

        for target_movie in unrated_movies:
            target_idx = movie_index_map[target_movie]
            similarities = []

            for rated_movie in rated_movies:
                rated_idx = movie_index_map[rated_movie]
                sim = self.item_similarity[target_idx, rated_idx]
                rating = user_row[rated_movie]
                similarities.append((sim, rating))

            if not similarities:
                continue

            sims = np.array([x[0] for x in similarities])
            ratings = np.array([x[1] for x in similarities])

            denom = np.sum(np.abs(sims))
            if denom > 0:
                predicted_rating = np.sum(sims * ratings) / denom
                predicted_scores.append((target_movie, predicted_rating))

        predicted_scores.sort(key=lambda x: x[1], reverse=True)
        return predicted_scores[:top_k]

    def evaluate(self, algorithm="user_based", top_k=10, positive_threshold=4.0):
        """
        评估指标：
        - Precision@K
        - Recall@K
        - HitRate@K

        这里采用 leave-one-out：
        每个用户最后一条评分为测试集
        若测试电影评分 >= positive_threshold，则视为正样本
        """
        if self.test_df is None:
            raise ValueError("请先划分训练测试集")

        test_positive = self.test_df[self.test_df["rating"] >= positive_threshold]

        if test_positive.empty:
            print("没有满足阈值的测试正样本，无法评估")
            return None

        hits = 0
        total_users = 0

        for _, row in test_positive.iterrows():
            user_id = row["userId"]
            true_movie = row["movieId"]

            if algorithm == "user_based":
                recommendations = self.recommend_user_based(user_id, top_k=top_k)
            elif algorithm == "item_based":
                recommendations = self.recommend_item_based(user_id, top_k=top_k)
            else:
                raise ValueError("algorithm 必须是 'user_based' 或 'item_based'")

            recommended_movie_ids = [movie_id for movie_id, _ in recommendations]

            if true_movie in recommended_movie_ids:
                hits += 1

            total_users += 1

        precision = hits / (total_users * top_k) if total_users > 0 else 0
        recall = hits / total_users if total_users > 0 else 0
        hit_rate = hits / total_users if total_users > 0 else 0

        result = {
            "algorithm": algorithm,
            "top_k": top_k,
            "test_users": total_users,
            "hits": hits,
            "precision_at_k": round(precision, 4),
            "recall_at_k": round(recall, 4),
            "hit_rate_at_k": round(hit_rate, 4),
        }

        return result

    def get_movie_title(self, movie_id):
        row = self.movies_df[self.movies_df["movieId"] == movie_id]
        if row.empty:
            return f"movieId={movie_id}"
        return row.iloc[0]["title"]

    def show_recommendations_for_user(self, user_id=1, top_k=10):
        print(f"\n===== 给用户 {user_id} 的推荐结果 =====")

        print("\n[基于用户的协同过滤]")
        user_recs = self.recommend_user_based(user_id, top_k=top_k)
        for rank, (movie_id, score) in enumerate(user_recs, start=1):
            print(f"{rank}. {self.get_movie_title(movie_id)} | 预测分数: {score:.4f}")

        print("\n[基于物品的协同过滤]")
        item_recs = self.recommend_item_based(user_id, top_k=top_k)
        for rank, (movie_id, score) in enumerate(item_recs, start=1):
            print(f"{rank}. {self.get_movie_title(movie_id)} | 预测分数: {score:.4f}")


def main():
    trainer = MovieLensCFTrainer()

    trainer.load_data()
    trainer.preprocess_data(min_user_ratings=5)
    trainer.train_test_split_leave_one_out()
    trainer.build_matrix()
    trainer.calculate_similarity()

    print("\n===== 评估结果 =====")
    user_result = trainer.evaluate(algorithm="user_based", top_k=10, positive_threshold=4.0)
    item_result = trainer.evaluate(algorithm="item_based", top_k=10, positive_threshold=4.0)

    print("\n[User-Based]")
    print(user_result)

    print("\n[Item-Based]")
    print(item_result)

    trainer.show_recommendations_for_user(user_id=1, top_k=10)


if __name__ == "__main__":
    main()