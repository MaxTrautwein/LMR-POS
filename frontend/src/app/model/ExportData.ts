import {ExportItem} from "./ExportItem";

export interface ExportData {
  id: number;
  saleDay: number;
  saleMonth: number;
  entryDay: number
  entryMonth: number;
  description: string;
  total: number;
  tax: number;
  saleDate: any;
  items: ExportItem[];
}

export interface ExportPageData extends ExportData {
  bookkeepingId: number;
}
