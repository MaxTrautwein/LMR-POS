import {Component, Input, input} from '@angular/core';
import {CartItem} from "../../../model/cartItem";

@Component({
  selector: 'app-cart-item',
  standalone: true,
  imports: [],
  templateUrl: './cart-item.component.html',
  styleUrl: './cart-item.component.css'
})
export class CartItemComponent {

  @Input() item!: CartItem;



}
