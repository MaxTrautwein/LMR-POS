import { ExportPageData} from "./ExportData";

export class ExportPage{

  public static pageSize = 60;
  public space: number;
  public items: ExportPageData[] = [];

  constructor() {
    this.space = ExportPage.pageSize;
    this.items = [];
  }

}
