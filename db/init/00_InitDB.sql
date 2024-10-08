DROP TABLE IF EXISTS SpecificToGroup;
DROP TABLE IF EXISTS SpecificItemTag;
DROP TABLE IF EXISTS Purchase;
DROP TABLE IF EXISTS Supplier;
DROP TABLE IF EXISTS Barcode;
DROP TABLE IF EXISTS FeatureTag;
DROP TABLE IF EXISTS ItemPriceHistory;
DROP TABLE IF EXISTS Transaction_Position;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Position;
DROP TABLE IF EXISTS SpecificItem;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS ItemGroup;
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
comment on column Tax.deprecatedDate IS 'if deprecated ; Document the Date where that took effect';

create TABLE Supplier
(
    id serial primary key,
    name text not null,
    url text, -- Web Page where we buy
    notes text -- In case we want to leave internal notes about Suppliers
);

comment on column Supplier.url is 'Web Page where we buy';

-- An Actual Product that we can Buy
-- Delete is not allowed
CREATE TABLE SpecificItem
(
    id          serial PRIMARY KEY,
    name        text NOT NULL,
    bon_name     text, -- If Set overrides whatever is set in the Group
    min_cnt      integer, -- (override) How much do we want to have in Stock
    manufacturer    integer references Manufacturer (id),
    itemBuyURL text, -- Optional buy URL of this Item
    itemURL text, -- Optional URL of this Item with Data for it
    notes text -- In case we want to note some stuff down
);

comment on column SpecificItem.bon_name IS 'override itemGroup bon_name';
comment on column SpecificItem.min_cnt IS 'override itemGroup min_cnt';
comment on column SpecificItem.itemBuyURL IS 'optional where to buy URL';
comment on column SpecificItem.itemURL IS 'optional details URL';

CREATE TABLE Barcode
(
    id serial PRIMARY KEY,
    code text not null, -- The Barcode Itself
    product integer references SpecificItem(id) not null
);

create TABLE FeatureTag -- Some Important Fact about a SpecificItem
(
    id serial PRIMARY KEY,
    tag text not null  -- The Fact (A4, White, green, Thick, thin, HB, 0.5mm)
);

comment on column FeatureTag.tag IS 'The Fact (A4, White, green, Thick, thin, HB, 0.5mm)';

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

comment on column Purchase.buyPrice IS 'INCLUDING TAX - use 0 to mark as unknown';


CREATE TABLE ItemGroup -- A Item Group, Specific Items with a common Name,
-- the same price and maybe the same Bon Name
-- If the Item Group is Linked to a Sale it MUST NOT be Deleted
-- It may be Deprecated
(
    id           serial PRIMARY KEY,
    name         text NOT NULL, -- How is that called? as what do we Label This?
    bon_name     text, -- There is limited Space on the Bon; Maybe We should select that DataType to limit the Chars
    min_cnt      integer not null, -- How much do we want to have in Stock
    deprecated   boolean default false -- If No Longer In Use
);


create TABLE SpecificToGroup -- Link one or more SpecificItem's to a Item Group
-- DO NOT delete, Deprecate Instead
-- May ONLY be deleted if the "Item" has been deleted
(
    id          serial primary key,
    itemGroup      integer references ItemGroup(id)    not null,
    specific    integer references SpecificItem(id) not null,
    deprecated  timestamp -- If No Longer In Use, Preserve History
);

create TABLE ItemPriceHistory -- We may need to Update Prices every now and then
-- When we do that we would still want to know the Real Price of an Old Transaction
-- To Not Duplicate Data we Shall Document Price Changes of the Things we Sell
-- May ONLY be deleted if the "Item" has been deleted
(
    id serial PRIMARY KEY,
    item integer references ItemGroup(id) not null,
    price numeric                         NOT NULL, -- Our Sell Price including Tax
    tax integer references Tax(id)        not null,
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
    product integer references SpecificItem (id) not null,
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
-- Probably beset to Use some process that enforces this
-- if there is a Valid reason to go against that, it shall be done manually by someone that knows what they are doing

-- TODO Maybe add Views to Simplify some Access

-- Get Tags Linked to a Specific Item
CREATE OR REPLACE FUNCTION GetLinkedTags(specificItemID int)
returns table (tag text)
as $$
    begin
        return query select f.tag
                     from featuretag f, specificitemtag s
                     where f.id = s.tag
                               and specificItemID = s.item;
    end;
    $$ language plpgsql;

-- Get the ID of an Item By Barcode
-- Returns Nothing if it doesn't exist
CREATE OR REPLACE FUNCTION GetSpecificItemID(barcodeScan text)
returns table (id integer)
as $$
    begin
        return query select b.product from barcode b where b.code = barcodeScan;
    end;
    $$ language plpgsql;

-- Get the Item Price & Tax amount for a Item ID
CREATE OR REPLACE FUNCTION GetCurrentSpecificItemPriceAndTax(specificItemID int)
returns table (price numeric, tax numeric)
as $$
    begin
        return query select h.price, t.amount from specifictogroup s, itemgroup g, itempricehistory h, tax t
         where s.specific = specificItemID and s.deprecated is NULL and g.deprecated = false
           and h.deprecateddate is null and s.itemgroup = g.id and g.id = h.item and t.id = h.tax ;
    end;
    $$ language plpgsql;


CREATE OR REPLACE FUNCTION GetBonName(specificItemID int)
returns table (bonName text)
as $$
    begin
        return query select coalesce(g.bon_name,s.bon_name) from SpecificItem s, itemgroup g, specifictogroup sg
                                                            where s.id = specificItemID and s.id = sg.specific
                                                              and sg.itemgroup = g.id and g.deprecated = false
                                                              and sg.deprecated is NULL;
    end;
    $$ language plpgsql;


CREATE OR REPLACE FUNCTION GetCurrentSpecificItemGroup(specificItemID int)
returns table (id integer)
as $$
    begin
        return query select g.itemgroup from specifictogroup g where g.specific = specificItemID and
                                                                     g.deprecated is null;
    end;
    $$ language plpgsql;


CREATE OR REPLACE FUNCTION GetSpecificItemPriceAndTax(specificItemID int, pointInTime timestamp)
returns table (price numeric, tax numeric)
as $$
    begin
        return query select h.price, t.amount from itempricehistory h, tax t, itemgroup g
         where t.id = h.tax and g.id = h.item and
               g.id = (select s.itemgroup from specifictogroup s where specific = specificItemID and
                                    coalesce(s.deprecated, clock_timestamp() + interval '1 year') > (pointInTime)
                              order by s.deprecated limit 1)
               and
               coalesce(h.deprecateddate, clock_timestamp() + interval '1 year') > (pointInTime) order by h.deprecateddate limit 1;
    end;
    $$ language plpgsql;


CREATE OR REPLACE FUNCTION GetTransactionsAfter(transactionID int)
returns table (saleDay numeric, saleMonth numeric, bookDay numeric, bookMonth numeric, id integer)
as $$
    begin
        return query SELECT extract(day  from transaction.sale_date),
            extract(month  from transaction.sale_date),
            extract(day  from clock_timestamp()),
            extract(month  from clock_timestamp()),
            transaction.id
            from transaction_position , position, transaction
             where transaction_position.trans = transaction.id and transaction_position.pos = position.id
             and transaction.id > transactionID
             group by transaction.sale_date, transaction.id order by transaction.sale_date;
    end;
    $$ language plpgsql;
