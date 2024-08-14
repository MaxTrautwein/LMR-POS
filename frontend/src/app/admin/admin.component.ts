import { Component } from '@angular/core';
import {RouterLink} from "@angular/router";
import {ApiService} from "../pos/api.service";

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    RouterLink
  ],
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})
export class AdminComponent {

  constructor(protected api: ApiService) {}
  protected OpenDrawer(){
    this.api.openDrawer();
  }
}
