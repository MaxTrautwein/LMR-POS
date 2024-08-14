import {Component, ViewChild} from '@angular/core';
import {CartService} from "../pos/cart.service";
import {ApiService} from "../pos/api.service";
import {ExportPdfService} from "../export-pdf.service";
import {ExportPdfComponent} from "./export-pdf/export-pdf.component";

@Component({
  selector: 'app-sales-export',
  standalone: true,
  imports: [
    ExportPdfComponent
  ],
  templateUrl: './sales-export.component.html',
  styleUrl: './sales-export.component.css'
})
export class SalesExportComponent {

  protected Output : string = "";
  // PoS Transaction
  @ViewChild('SaleID') saleId: any;
  // Bookkeeping Transaction
  @ViewChild('TransactionID') TransactionID: any;


  PDF_RequestJson = []

  constructor(private api: ApiService, protected exportPdf: ExportPdfService) {}

  protected ExportData(): void {

    this.api.getExportData(this.saleId.nativeElement.value).subscribe(items => {
      this.exportPdf.prepareExportData(items,this.TransactionID.nativeElement.value)
      this.Output = this.exportPdf.getAndCopyBookkeepingString()
    })
  }


  protected readonly window = window;
}
