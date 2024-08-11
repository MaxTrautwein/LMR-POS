import { Routes } from '@angular/router';
import {AppComponent} from "./app.component";
import {PosComponent} from "./pos/pos.component";
import {SalesExportComponent} from "./sales-export/sales-export.component";
import {AdminComponent} from "./admin/admin.component";

export const routes: Routes = [
  { path: '', component: PosComponent },
  { path: 'Export', component: SalesExportComponent},
  { path: 'Admin', component: AdminComponent }
];
