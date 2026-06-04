export interface FormatInfoModel {
  isAvailable: boolean;
  acsTokenLink: string | null;
}

export interface AccessInfoModel {
  country: string | null;
  viewability: string | null;
  embeddable: boolean;
  publicDomain: boolean; // public_domain
  epub: FormatInfoModel | null;
  pdf: FormatInfoModel | null;
  webReaderLink: string | null; // web_reader_link
}

export interface CreateAccessInfoRequest {
  book_id: number;
  access_info: AccessInfoModel;
}

export interface UpdateAccessInfoRequest {
  access_info_id: number;
  access_info: AccessInfoModel;
}
