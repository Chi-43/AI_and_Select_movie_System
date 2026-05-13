<template>
  <div class="admin-community">
    <div class="tab-bar">
      <button :class="{ active: tab === 'topics' }" @click="tab = 'topics'">
        话题管理
      </button>
      <button :class="{ active: tab === 'posts' }" @click="tab = 'posts'">
        帖子管理
      </button>
      <button :class="{ active: tab === 'replies' }" @click="tab = 'replies'">
        回复管理
      </button>
    </div>

    <!-- 话题管理 -->
    <div v-if="tab === 'topics'" class="section">
      <div class="form-row">
        <input v-model="topicForm.name" placeholder="话题名称" />
        <input v-model="topicForm.description" placeholder="话题描述" />
        <input v-model="topicForm.icon" placeholder="图标" class="icon-input" />
        <button
          @click="topicForm.editingId ? updateTopic() : createTopic()"
          class="primary-btn"
          :disabled="!topicForm.name.trim()"
        >
          {{ topicForm.editingId ? "保存修改" : "创建话题" }}
        </button>
        <button
          v-if="topicForm.editingId"
          @click="resetTopicForm"
          class="cancel-btn"
        >
          取消
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>图标</th>
            <th>名称</th>
            <th>描述</th>
            <th>帖子数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in topics" :key="t.id">
            <td>{{ t.icon }}</td>
            <td>{{ t.name }}</td>
            <td>{{ t.description }}</td>
            <td>{{ t.post_count }}</td>
            <td class="actions">
              <button @click="editTopic(t)">编辑</button>
              <button class="danger" @click="deleteTopic(t.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 帖子管理 -->
    <div v-if="tab === 'posts'" class="section">
      <table>
        <thead>
          <tr>
            <th>标题</th>
            <th>作者</th>
            <th>话题</th>
            <th>浏览</th>
            <th>回复</th>
            <th>赞</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in posts" :key="p.id">
            <td class="title-cell">{{ p.title }}</td>
            <td>{{ p.created_by }}</td>
            <td>{{ p.topic }}</td>
            <td>{{ p.view_count }}</td>
            <td>{{ p.reply_count }}</td>
            <td>{{ p.like_count }}</td>
            <td class="actions">
              <button class="danger" @click="deletePost(p.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 回复管理 -->
    <div v-if="tab === 'replies'" class="section">
      <table>
        <thead>
          <tr>
            <th>内容</th>
            <th>作者</th>
            <th>所属帖子</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in replies" :key="r.id">
            <td class="title-cell">{{ r.content }}</td>
            <td>{{ r.created_by }}</td>
            <td>{{ r.post_title }}</td>
            <td>{{ formatDate(r.created_at) }}</td>
            <td class="actions">
              <button class="danger" @click="deleteReply(r.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
const API = "http://127.0.0.1:8000";
export default defineComponent({
  name: "AdminCommunityView",
  setup() {
    const tab = ref("topics");
    const topics = ref<any[]>([]);
    const posts = ref<any[]>([]);
    const replies = ref<any[]>([]);
    const topicForm = ref({
      editingId: null as number | null,
      name: "",
      description: "",
      icon: "💬",
    });

    const headers = () => {
      const token = localStorage.getItem("admin_token");
      return {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      };
    };

    const fetchTopics = async () => {
      const r = await fetch(`${API}/api/admin/topics/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem("admin_token")}`,
        },
      });
      if (r.ok) {
        const d = await r.json();
        topics.value = d.topics || [];
      }
    };

    const createTopic = async () => {
      await fetch(`${API}/api/admin/topics/`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify(topicForm.value),
      });
      resetTopicForm();
      await fetchTopics();
    };

    const editTopic = (t: any) => {
      topicForm.value = {
        editingId: t.id,
        name: t.name,
        description: t.description,
        icon: t.icon,
      };
    };

    const updateTopic = async () => {
      await fetch(`${API}/api/admin/topics/`, {
        method: "PUT",
        headers: headers(),
        body: JSON.stringify({
          topic_id: topicForm.value.editingId,
          ...topicForm.value,
        }),
      });
      resetTopicForm();
      await fetchTopics();
    };

    const deleteTopic = async (id: number) => {
      if (!confirm("确定删除该话题及其所有帖子？")) return;
      await fetch(`${API}/api/admin/topics/?topic_id=${id}`, {
        method: "DELETE",
        headers: headers(),
      });
      await fetchTopics();
    };

    const resetTopicForm = () => {
      topicForm.value = {
        editingId: null,
        name: "",
        description: "",
        icon: "💬",
      };
    };

    const fetchPosts = async () => {
      const r = await fetch(`${API}/api/admin/posts/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem("admin_token")}`,
        },
      });
      if (r.ok) {
        const d = await r.json();
        posts.value = d.posts || [];
      }
    };

    const deletePost = async (id: number) => {
      if (!confirm("确定删除该帖子？")) return;
      await fetch(`${API}/api/admin/posts/?post_id=${id}`, {
        method: "DELETE",
        headers: headers(),
      });
      await fetchPosts();
    };

    const fetchReplies = async () => {
      const r = await fetch(`${API}/api/admin/replies/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem("admin_token")}`,
        },
      });
      if (r.ok) {
        const d = await r.json();
        replies.value = d.replies || [];
      }
    };

    const deleteReply = async (id: number) => {
      if (!confirm("确定删除该回复？")) return;
      await fetch(`${API}/api/admin/replies/?reply_id=${id}`, {
        method: "DELETE",
        headers: headers(),
      });
      await fetchReplies();
    };

    const formatDate = (d: string) => new Date(d).toLocaleDateString("zh-CN");

    onMounted(async () => {
      await fetchTopics();
      await fetchPosts();
      await fetchReplies();
    });
    return {
      tab,
      topics,
      posts,
      replies,
      topicForm,
      createTopic,
      editTopic,
      updateTopic,
      deleteTopic,
      resetTopicForm,
      deletePost,
      deleteReply,
      formatDate,
    };
  },
});
</script>

<style scoped>
.admin-community {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.tab-bar {
  display: flex;
  gap: 4px;
  background: var(--nav-hover-bg);
  border-radius: var(--radius-md);
  padding: 4px;
  width: fit-content;
}
.tab-bar button {
  border: none;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.tab-bar button.active {
  background: var(--panel-bg);
  color: var(--text-primary);
  box-shadow: var(--panel-shadow);
}
.section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.form-row input {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text-primary);
  outline: none;
}
.form-row input:focus {
  border-color: var(--input-focus-border);
}
.icon-input {
  width: 70px;
  text-align: center;
}
.primary-btn,
.cancel-btn {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.primary-btn {
  background: var(--primary-gradient);
  color: #fff;
}
.cancel-btn {
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}
.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
table {
  width: 100%;
  border-collapse: collapse;
  background: var(--panel-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
th {
  text-align: left;
  padding: 12px 14px;
  background: var(--nav-hover-bg);
  color: var(--text-secondary);
  font-size: 0.85rem;
}
td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--panel-border);
  color: var(--text-primary);
  font-size: 0.9rem;
}
.title-cell {
  max-width: 280px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.actions {
  display: flex;
  gap: 8px;
}
.actions button {
  border: none;
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  background: var(--nav-hover-bg);
  color: var(--text-primary);
}
.actions button.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
</style>
