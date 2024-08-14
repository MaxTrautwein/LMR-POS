import { Injectable } from '@angular/core';
import {CartItem} from "../model/cartItem";
import {mergeMap, Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {ExportItem} from "../model/ExportItem";
import {ExportData} from "../model/ExportData";

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  server = "http://localhost:5000"

  constructor(private http: HttpClient) { }


  public getItem(barcode: string): Observable<CartItem> {
   return <Observable<CartItem>>this.http.get(this.server + '/item?code=' + barcode)
  }

  // TODO Get a Proper Return here. --> for now just log it
  public makeSale(cart: CartItem[]) {
    this.http.post(this.server + '/make_sale', cart).subscribe(response =>
      console.log(response)
    )
  }

  public getExportData(id: number): Observable<ExportData[]> {
    return <Observable<ExportData[]>>this.http.get(this.server + "/Export" + "?id=" + id)
  }




}
