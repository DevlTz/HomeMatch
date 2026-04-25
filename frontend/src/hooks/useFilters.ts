import { useState, useCallback } from "react";
import type { Filters } from "../types";
import { DEFAULT_FILTERS } from "../data/properties";

export function useFilters() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);

  const setPurpose = useCallback((purpose: Filters["purpose"]) => {
    setFilters((prev) => ({ ...prev, purpose }));
  }, []);

  const setBeds = useCallback((beds: number) => {
    setFilters((prev) => ({ ...prev, beds }));
  }, []);

  const setSuites = useCallback((suites: number) => {
    setFilters((prev) => ({ ...prev, suites }));
  }, []);

  const setParking = useCallback((parking: number) => {
    setFilters((prev) => ({ ...prev, parking }));
  }, []);

  const toggleExtra = useCallback((extra: string) => {
    setFilters((prev) => ({
      ...prev,
      extras: prev.extras.includes(extra)
        ? prev.extras.filter((e) => e !== extra)
        : [...prev.extras, extra],
    }));
  }, []);

  const setMaxPrice = useCallback((maxPrice: number) => {
    setFilters((prev) => ({ ...prev, maxPrice }));
  }, []);

  const setMaxArea = useCallback((maxArea: number) => {
    setFilters((prev) => ({ ...prev, maxArea }));
  }, []);

  const reset = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  return {
    filters,
    setPurpose,
    setBeds,
    setSuites,
    setParking,
    toggleExtra,
    setMaxPrice,
    setMaxArea,
    reset,
  };
}
