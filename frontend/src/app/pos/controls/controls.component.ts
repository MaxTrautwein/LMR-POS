import { Component } from '@angular/core';
import {CartService} from "../cart.service";
import {ApiService} from "../api.service";

@Component({
  selector: 'app-controls',
  standalone: true,
  imports: [],
  templateUrl: './controls.component.html',
  styleUrl: './controls.component.css'
})
export class ControlsComponent {

  constructor(protected cartService: CartService, private api: ApiService) {}


  protected makeSale(){
    this.api.makeSale(this.cartService.getCart())
    // TODO: TEMP for Debugging
    // this.cartService.EmptyCart()
  }


}
