DROP TABLE IF EXISTS SpecificToPseudo;
DROP TABLE IF EXISTS SpecificItemTag;
DROP TABLE IF EXISTS ProductBarcodes;
DROP TABLE IF EXISTS Purchase;
DROP TABLE IF EXISTS SpecificItem;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS Supplier;
DROP TABLE IF EXISTS Barcode;
DROP TABLE IF EXISTS FeatureTag;
DROP TABLE IF EXISTS ItemPriceHistory;
DROP TABLE IF EXISTS Transaction_Position;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Position;
DROP TABLE IF EXISTS Item;
DROP TABLE IF EXISTS Tax;


-- We expect to have a Manufacturer for more then one item.
-- It might be better to separate them out just in case
CREATE TABLE Manufacturer
(
    id serial PRIMARY KEY,
    name text not NULL
);

CREATE TABLE Tax -- DO NOT delete Entry's, if they are no longer Valid Deprecate Them, And Create an Updated Value
(
    id serial PRIMARY KEY,
    name text not NULL,
    amount numeric not null,
    deprecatedDate timestamp -- if deprecated ; Document the Date where that took effect
);

create TABLE Supplier
(
    id serial primary key,
    name text not null,
    url text, -- Web Page where we buy
    notes text -- In case we want to leave internal notes about Suppliers
);

-- An Actual Product that we can Buy
-- Delete is not allowed
CREATE TABLE SpecificItem
(
    id          serial PRIMARY KEY,
    name        text NOT NULL,
    manufacturer    integer references Manufacturer (id),
    itemBuyURL text, -- Optional buy URL of this Item
    itemURL text, -- Optional URL of this Item with Data for it
    notes text -- In case we want to note some stuff down
);


CREATE TABLE Barcode
(
    id serial PRIMARY KEY,
    code text not null -- The Barcode Itself
);

CREATE TABLE ProductBarcodes -- A Single Product can have more then one Barcode
-- Special Barcodes might apply to a Pseudo Item int turn affecting more then one SpecificItem
-- That might be required if a Barcode is not available
(
    id serial PRIMARY KEY,
    product integer references SpecificItem(id) not null ,
    code integer references Barcode(id) not null
);

create TABLE FeatureTag -- Some Important Fact about a SpecificItem
(
    id serial PRIMARY KEY,
    tag text not null  -- The Fact (A4, White, green, Thick, thin, HB, 0.5mm)
);

create TABLE SpecificItemTag -- Map Tags to Items
(
    id serial PRIMARY KEY,
    tag integer references FeatureTag(id),
    item integer references SpecificItem(id)
);

create TABLE Purchase
(
    id serial PRIMARY KEY,
    specificItem integer references SpecificItem(id) not null,
    cnt integer not null, -- The amount that we bought
    dateAdded timestamp, -- when did wie add this?
    dateBuy timestamp,  -- when was this bought?
    supplier integer references Supplier(id) not null,
    buyPrice numeric not null, -- INCLUDING TAX - use 0 to mark as unknown
    tax integer references Tax(id) not null,
    notes text -- in case of other Notes
);



CREATE TABLE Item -- A Pseudo Item; Just the Item that we Sell, not specifically linked to a Manufacturer
-- If the Pseudo Item is Linked to a Sale it MUST NOT be Deleted
-- It may be Deprecated
(
    id           serial PRIMARY KEY,
    name         text NOT NULL, -- How is that called? as what do we Label This?
    bon_name     text, -- There is limited Space on the Bon; Maybe We should select that DataType to limit the Chars
    min_cnt      integer not null, -- How much do we want to have in Stock
    deprecated   boolean default false -- If No Longer In Use
);


create TABLE SpecificToPseudo -- Link one or more SpecificItem's to a Pseudo Item
-- DO NOT delete, Deprecate Instead
-- May ONLY be deleted if the "Item" has been deleted
(
    id          serial primary key,
    pseudo      integer references Item(id) not null,
    specific    integer references SpecificItem(id) not null,
    deprecated  timestamp -- If No Longer In Use, Preserve History
);

create TABLE ItemPriceHistory -- We may need to Update Prices every now and then
-- When we do that we would still want to know the Real Price of an Old Transaction
-- To Not Duplicate Data we Shall Document Price Changes of the Things we Sell
-- May ONLY be deleted if the "Item" has been deleted
(
    id serial PRIMARY KEY,
    item integer references Item(id)  not null,
    price numeric NOT NULL, -- Our Sell Price including Tax
    tax integer references Tax(id) not null,
    deprecatedDate timestamp -- if deprecated; Document the Date where that took effect
);


--One Sale Transaction
create TABLE Transaction -- TODO Add stuff we probably need for TSE
(
    id        serial primary key,
    personal  text not null, --Name of the Person Performing the Sale
    sale_date timestamp ,     --When did this sale occur
    notes text -- in case of other Notes -- Emergency Use only
);

-- Item of a Transaction
CREATE TABLE Position
(
    id      serial PRIMARY KEY,
    product integer references Item (id) not null,
    count   integer                       not null
);

-- Relationship between Transactions and Positions
create TABLE Transaction_Position
(
    id    serial primary key,
    pos   integer references position (id)    not null,
    trans integer references Transaction (id) not null
);

-- TODO Maybe add ways to enforce the described rules
-- But DON'T USE "rules" as according to some online Reports they break "... retuning ..."
-- A very useful feature that we also use a lot...

-- TODO Maybe add Views to Simplify some Access

-- Get Tags Linked to a Specific Item
CREATE OR REPLACE FUNCTION GetLinkedTags(specificitemID int)
returns table (tag text)
language plpgsql
as $$
    begin
        return query select featuretag.tag
                     from featuretag, specificitemtag
                     where featuretag.id = specificitemtag.tag
                               and specificitemID = specificitemtag.item;
    end;
    $$