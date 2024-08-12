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

  handleBarcode(code: string){
    this.api.getItem(code).subscribe(item => {
        item.cnt = 1
        this.cartService.AddItem(item)
    })
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
