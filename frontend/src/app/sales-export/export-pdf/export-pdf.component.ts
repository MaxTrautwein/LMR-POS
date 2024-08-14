import { Component } from '@angular/core';
import {ExportPdfService} from "../../export-pdf.service";

@Component({
  selector: 'app-export-pdf',
  standalone: true,
  imports: [],
  templateUrl: './export-pdf.component.html',
  styleUrl: './export-pdf.component.css'
})
export class ExportPdfComponent {

  constructor(protected exportPdf: ExportPdfService) {

  }


}
