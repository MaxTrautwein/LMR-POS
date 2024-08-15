import {Component, HostListener} from '@angular/core';
import {CartComponent} from "./cart/cart.component";
import {ControlsComponent} from "./controls/controls.component";
import {CartItem} from "../model/cartItem";
import {CartService} from "./cart.service";
import {ApiService} from "./api.service";

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [
    CartComponent,
    ControlsComponent
  ],
  templateUrl: './pos.component.html',
  styleUrl: './pos.component.css'
})
export class PosComponent {

  private handleNewItem(code: string): void {
    this.api.getItem(code).subscribe(item => {
      item.cnt = 1
      this.cartService.AddItem(item)
    })
  }

  private handelBarcodeControls(code: string): void {
    switch(code) {
      case "LMR-POS-cancel":
        this.cartService.RemoveLastItem()
        break
      case "LMR-POS-Clear":
        this.cartService.EmptyCart()
        break
      case "LMR-POS-Sale":
        this.cartService.makeSale()
        break
      case "LMR-POS-Logout":
        // Logout is not Implemented, so ignore it for now
        break
    }
  }

  private handelItemCountControls(code: string): void {
    const amount = Number(code.replace("LMR-ADD-",""));
    this.cartService.UpdateLastItemCnt(amount)
  }

  private handleBarcode(code: string){
    code = code.replace("ß","-") // Codes where printed with 'ß' instead of '-'

    if (code.startsWith("LMR-POS")){
      this.handelBarcodeControls(code)
    }else if (code.startsWith("LMR-ADD-")){
      this.handelItemCountControls(code)
    }else{
      // Regular Barcode
      this.handleNewItem(code)
    }
  }


  constructor(protected cartService: CartService, private api: ApiService) {}


  keyboardInput: string = "";

  @HostListener('document:keypress', ['$event'])
  ListenForBarCode(event: KeyboardEvent) {
    if (event.key === 'Enter') {

      // TODO Send Request to add item to cart
      console.log(this.keyboardInput);
      this.handleBarcode(this.keyboardInput);

      this.keyboardInput = "";
    }else {
      this.keyboardInput += event.key;
    }
  }

}
