export type IdentifierType = "ISBN_10" | "ISBN_13" | "OTHER";

export interface IndustryIdentifier {
  type: IdentifierType;
  identifier: string;
}
