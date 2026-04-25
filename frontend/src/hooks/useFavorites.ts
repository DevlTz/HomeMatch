import { useState, useCallback } from "react";

export function useFavorites() {
  const [favorites, setFavorites] = useState<Set<number>>(new Set());

  const toggle = useCallback((id: number) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  const isFavorite = useCallback(
    (id: number) => favorites.has(id),
    [favorites]
  );

  return { favorites, toggle, isFavorite };
}
