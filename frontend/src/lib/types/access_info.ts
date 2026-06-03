export interface FormatInfoModel {
  isAvailable: boolean;
  acsTokenLink: string | null;
}

export interface AccessInfoModel {
  country: string | null;
  viewability: string | null;
  embeddable: boolean;
  public_domain: boolean;
  epub: FormatInfoModel | null;
  pdf: FormatInfoModel | null;
  web_reader_link: string | null;
}

export interface CreateAccessInfoRequest {
  book_id: number;
  access_info: AccessInfoModel;
}

export interface UpdateAccessInfoRequest {
  access_info_id: number;
  access_info: AccessInfoModel;
}
