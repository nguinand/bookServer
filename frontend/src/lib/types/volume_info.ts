import type { IndustryIdentifier } from "./identifiers";

export interface ImageLinksModel {
  smallThumbnail: string | null; // small_thumbnail
  thumbnail: string | null;
}

export interface VolumeInfoModel {
  title: string;
  subtitle: string | null;
  authors: string[];
  publisher: string | null;
  publishedDate: string | null; // published_date
  description: string | null;
  pageCount: number | null; // page_count
  categories: string[];
  averageRating: number | null; // average_rating
  ratingsCount: number | null; // ratings_count
  imageLinks: ImageLinksModel | null; // image_links
  previewLink: string | null; // preview_link
  infoLink: string | null; // info_link
  language: string | null;
  industryIdentifiers: IndustryIdentifier[] | null;
  maturity_rating: string | null;
}
