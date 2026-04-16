import { defineStore } from "pinia";
import { ref, computed } from "vue";

export type ThemeMode = "light" | "dark";

export const useThemeStore = defineStore("theme", () => {
  const theme = ref<ThemeMode>("dark");

  const isDark = computed(() => theme.value === "dark");

  const setTheme = (newTheme: ThemeMode) => {
    theme.value = newTheme;
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  };

  const toggleTheme = () => {
    setTheme(theme.value === "dark" ? "light" : "dark");
  };

  const initialize = () => {
    const saved = localStorage.getItem("theme") as ThemeMode | null;
    if (saved && (saved === "light" || saved === "dark")) {
      setTheme(saved);
    } else if (window.matchMedia("(prefers-color-scheme: light)").matches) {
      setTheme("light");
    } else {
      setTheme("dark");
    }
  };

  return { theme, isDark, setTheme, toggleTheme, initialize };
});
