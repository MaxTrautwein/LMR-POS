import { Injectable } from '@angular/core';
import {CartItem} from "../model/cartItem";
import {ApiService} from "./api.service";

@Injectable({
  providedIn: 'root'
})
export class CartService {

  constructor(private api: ApiService) { }

  items: CartItem[] = new Array<CartItem>();
  total: number = 0;

  private recalculatePrice(){
    this.total = 0;
    for(let item of this.items){
      this.total += item.price * item.cnt;
    }
  }

  public getPrice(): number {
    return this.total;
  }

  public getCart(): CartItem[]{
    return this.items;
  }

  public EmptyCart(){
    this.items.length = 0;
    this.recalculatePrice();
  }

  public RemoveLastItem(){
    this.items.pop();
    this.recalculatePrice();
  }

  public AddItem(item: CartItem){
    let itemIndex = -1;
    for (let i = 0; i < this.items.length; i++) {
      let CartItem = this.items[i];
      if (CartItem.id == item.id){
        itemIndex = i;
      }
    }

    if (itemIndex != -1){
      this.items[itemIndex].cnt++;
    }else {
      this.items.push(item);
    }
    this.recalculatePrice();
  }

  // Offset by Input
  public UpdateLastItemCnt(count: number){
    if (this.items.length === 0 || count === 0) {
      return;
    }
    let item: CartItem = this.items.pop()!
    item.cnt += count;
    if (item.cnt > 0){
      this.items.push(item);
    }
    this.recalculatePrice();
  }

  public makeSale(){
    this.api.makeSale(this.items)

    this.EmptyCart()
  }

}
