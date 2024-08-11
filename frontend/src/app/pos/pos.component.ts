import {Component, HostListener} from '@angular/core';
import {CartComponent} from "./cart/cart.component";
import {ControlsComponent} from "./controls/controls.component";
import {CartItem} from "../model/cartItem";
import {CartService} from "./cart.service";

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
    this.getItem(code);
  }


  async getItem(barcode: string){
    let server = "http://localhost:5000"

    let data = await fetch(server + '/item?code=' + barcode).then(res => res.json())
    console.log(data);
    let item: CartItem =  data;
    item.cnt = 1
    this.cartService.AddItem(item)
  }

  constructor(private cartService: CartService) {}


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
