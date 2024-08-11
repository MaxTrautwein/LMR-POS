import { Component } from '@angular/core';
import {CartItem} from "../../model/cartItem";
import {CartItemComponent} from "./cart-item/cart-item.component";
import {CartService} from "../cart.service";

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [
    CartItemComponent
  ],
  templateUrl: './cart.component.html',
  styleUrl: './cart.component.css'
})
export class CartComponent {
  constructor(protected cartService: CartService) {}

}
