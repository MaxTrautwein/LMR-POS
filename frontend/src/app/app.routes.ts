import { Routes } from '@angular/router';
import {AppComponent} from "./app.component";
import {PosComponent} from "./pos/pos.component";
import {SalesExportComponent} from "./sales-export/sales-export.component";
import {AdminComponent} from "./admin/admin.component";
import {ExportPdfComponent} from "./export-pdf/export-pdf.component";

export const routes: Routes = [
  { path: '', component: PosComponent },
  { path: 'Export', component: SalesExportComponent},
  { path: 'Export/pdf', component: ExportPdfComponent},
  { path: 'Admin', component: AdminComponent }
];
