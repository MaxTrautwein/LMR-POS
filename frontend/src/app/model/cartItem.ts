
export interface CartItem {
  id: number;
  name: string;
  bonName: string;
  price: number;
  tax: number;
  tags: string[];

  // Note: not set in "/item"
  cnt: number;

}
