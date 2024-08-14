import { Injectable } from '@angular/core';
import {ExportItem} from "./model/ExportItem";
import {ExportData, ExportPageData} from "./model/ExportData";
import {ExportPage} from "./model/ExportPage";

@Injectable({
  providedIn: 'root'
})
export class ExportPdfService {


  private BookkeepingString: string = "";
  public pageLayout: ExportPage[] = [];

  constructor() {
  }

  private CalculateExportTransactionSpace(SalePositions: number) {
    if (SalePositions <= 2) {
      return 17;
    }
    return 15 + SalePositions;
  }

  public prepareExportData(items: ExportData[], TransactionID: number) {
    TransactionID++;
    this.pageLayout = [];
    this.pageLayout.push(new ExportPage());
    this.BookkeepingString = "";
    for (let item of items) {
      let line: string = `\t${TransactionID}\t${item.saleDay}\t${item.saleMonth}\t`
      line +=  `${item.saleDay}\t${item.saleMonth}\t${item.description}; TaxRate:${item.tax}`
      line += `\t\t${item.total}`
      this.BookkeepingString += line + "\n"
      TransactionID++;

      let reqSpace = this.CalculateExportTransactionSpace(item.items.length)
      console.log(reqSpace);
      if (this.pageLayout.at(-1)!.space < reqSpace ){
        // Not enough Space Add new Page
        if (reqSpace > ExportPage.pageSize){
          alert("Transaction: " + TransactionID + " is too large\n" +
            "You need to manually Export it. Or the SW needs an Update");
          continue; // Skip that Printout
        }
        this.pageLayout.push(new ExportPage());
      }
      // We now have Enough space for That Transaction
      let pageData : ExportPageData = <ExportPageData>item;
      pageData.bookkeepingId = TransactionID - 1;

      this.pageLayout.at(-1)!.items.push(pageData);
      this.pageLayout.at(-1)!.space -= reqSpace;


    }
    console.log(this.pageLayout);

  }
  public getAndCopyBookkeepingString(){
    navigator.clipboard.writeText(this.BookkeepingString);
    return this.BookkeepingString;
  }


}
