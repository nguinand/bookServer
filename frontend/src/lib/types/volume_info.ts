import type { IndustryIdentifier } from "./identifiers";

export interface ImageLinksModel {
  smallThumbnail: string | null;
  thumbnail: string | null;
}

export interface VolumeInfoModel {
  title: string;
  subtitle: string | null;
  authors: string[];
  publisher: string | null;
  published_date: string | null;
  description: string | null;
  page_count: number | null;
  categories: string[];
  average_rating: number | null;
  ratings_count: number | null;
  image_links: ImageLinksModel | null;
  preview_link: string | null;
  info_link: string | null;
  language: string | null;
  industryIdentifiers: IndustryIdentifier[] | null;
  maturity_rating: string | null;
}
