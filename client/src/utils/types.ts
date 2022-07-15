export interface BondModel {
  model: string;
  pk: string;
  fields: {
    currency: string;
    price: number | string;
    updated: number;
  };
}

export interface DeskModel {
  model: string;
  pk: string;
  fields: {
    cash: string | number;
    updated: number;
  };
}

export interface TraderModel {
  model: string;
  pk: string;
  fields: {
    desk: string;
  };
}


export interface BookModel {
  model: string;
  pk: string;
  fields: {
    trader: string;
  };
}

export interface ExclusionModel {
  model: string;
  pk: string;
  fields: {
    desk: string;
    trader: string;
    book: string;
    buy_sell: string;
    quantity: number | string;
    bond: string;
    price: number | string | null;
    exclusion_type: string; 
  };
}

export interface BondRecordResponse {
  desk: DeskModel;
  trader: TraderModel;
  book: BookModel;
  bond: BondModel;
  position: number;
  NV: number;
}

export interface PositionLevelResponse {
  desk: string;
  trader: string;
  book: string
  position: number;
  NV: number;
}

export interface CurrencyLevelResponse {
  desk: string;
  currency: string;
  position: number;
  NV: number;
}

