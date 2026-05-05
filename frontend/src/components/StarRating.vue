<template>
  <div class="star-rating" :class="{ readonly }" :style="{ fontSize: size }">
    <span
      v-for="star in max"
      :key="star"
      class="star"
      :class="starClasses(star)"
      @click="handleClick(star, $event)"
      @mouseenter="hoverIndex = star"
      @mouseleave="hoverIndex = 0"
    >
      {{ starChar(star) }}
    </span>
    <span v-if="showLabel" class="rating-label">{{ displayLabel }}</span>
    <button
      v-if="!readonly && modelValue > 0"
      class="clear-btn"
      @click="clearRating"
    >
      清除
    </button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, PropType } from "vue";

export default defineComponent({
  name: "StarRating",
  props: {
    modelValue: { type: Number, default: 0 },
    max: { type: Number, default: 5 },
    readonly: { type: Boolean, default: false },
    size: { type: String, default: "1.4rem" },
    showLabel: { type: Boolean, default: false },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const hoverIndex = ref(0);

    const displayValue = computed(() =>
      hoverIndex.value > 0 ? hoverIndex.value : props.modelValue
    );

    const halfStarThreshold = 0.25;

    const starClasses = (star: number) => ({
      active: displayValue.value >= star,
      half:
        !(displayValue.value >= star) &&
        displayValue.value >= star - 0.5 + halfStarThreshold,
      hover: hoverIndex.value > 0 && hoverIndex.value >= star,
    });

    const starChar = (star: number) => {
      if (displayValue.value >= star) return "★";
      if (displayValue.value >= star - 0.5 + halfStarThreshold) return "★";
      return "☆";
    };

    const displayLabel = computed(() => {
      if (props.modelValue === 0) return "未评分";
      return props.modelValue.toFixed(1) + " / " + props.max;
    });

    const handleClick = (star: number, event: MouseEvent) => {
      if (props.readonly) return;

      const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
      const x = event.clientX - rect.left;
      const isLeftHalf = x < rect.width / 2;

      const newValue = isLeftHalf ? star - 0.5 : star;
      emit("update:modelValue", newValue);
    };

    const clearRating = () => {
      emit("update:modelValue", 0);
    };

    return {
      hoverIndex,
      starClasses,
      starChar,
      displayLabel,
      handleClick,
      clearRating,
    };
  },
});
</script>

<style scoped>
.star-rating {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  user-select: none;
}

.star-rating.readonly {
  pointer-events: none;
}

.star {
  cursor: pointer;
  color: #d1d5db;
  transition: color 0.15s ease, transform 0.15s ease;
  line-height: 1;
}

.star.active {
  color: #f59e0b;
}

.star.half {
  color: #fbbf24;
}

.star.hover {
  transform: scale(1.15);
}

.clear-btn {
  margin-left: 8px;
  padding: 2px 8px;
  font-size: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s ease;
}

.clear-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.rating-label {
  margin-left: 8px;
  font-size: 0.85em;
  color: #6b7280;
}
</style>
