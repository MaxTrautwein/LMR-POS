DROP TABLE IF EXISTS Barcodes;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Position;
DROP TABLE IF EXISTS Transaction_Position;

CREATE TABLE Items
(
    id           serial PRIMARY KEY,
    name         text                  NOT NULL,
    cnt          integer               NOT NULL,
    price        numeric                 NOT NULL,
    manufacturer text                  NOT NULL,
    color        text,
    min_cnt      integer               NOT NULL,
    details      text,
    size         text,
    tax          float4 DEFAULT '0.19' NOT NULL,
    bon_name    text
);

CREATE TABLE Barcodes
(
    id      serial PRIMARY KEY,
    barcode text                          NOT NULL,
    item    integer references Items (id) not null
);

--One Sale Transaction
create TABLE Transaction
(
    id        serial primary key,
    personal  text not null, --Name of the Person Performing the Sale
    sale_date timestamp      --When did this sale occur
);

-- Item of a Transaction
CREATE TABLE Position
(
    id      serial PRIMARY KEY,
    product integer references Items (id) not null,
    count   integer                       not null,
    total   numeric --Save Price as the Items price may change at any time
);

-- Relationship between Transactions and Positions
create TABLE Transaction_Position
(
    id    serial primary key,
    pos   integer references position (id)    not null,
    trans integer references Transaction (id) not null
);