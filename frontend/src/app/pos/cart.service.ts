import { Injectable } from '@angular/core';
import {CartItem} from "../model/cartItem";

@Injectable({
  providedIn: 'root'
})
export class CartService {

  constructor() { }

  items: CartItem[] = new Array<CartItem>();

  public getCart(): CartItem[]{
    return this.items;
  }

  public EmptyCart(){
    this.items.length = 0;
  }

  public RemoveLastItem(){
    this.items.pop();
  }

  public AddItem(item: CartItem){
    this.items.push(item);
  }

}
