import type { Filters } from "../types";

export const DEFAULT_FILTERS: Filters = {
  purpose: "buy",
  beds: 0,
  suites: 0,
  parking: 0,
  extras: [],
  minPrice: 0,
  maxPrice: 1_000_000,
  minArea: 0,
  maxArea: 500,
};
