export interface Property {
  id: number;
  title: string;
  location: string;
  bedrooms: number;
  suites: number;
  parking: number;
  area: number;
  price: number;
  highlight?: boolean;
  image: string;
}

export interface Filters {
  purpose: "buy" | "rent";
  beds: number;
  suites: number;
  parking: number;
  extras: string[];
  minPrice: number;
  maxPrice: number;
  minArea: number;
  maxArea: number;
}

export type Screen = "landing" | "search";
