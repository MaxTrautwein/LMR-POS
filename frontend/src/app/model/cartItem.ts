
export interface CartItem {

  name: string;
  bonName: string;

  price: number;
  tax: number;

  tags: string[];

  // Not sure how to best do that but that won't be transmitted
  cnt: number;

}
