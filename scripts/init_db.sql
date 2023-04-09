CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- item table
CREATE TABLE public.item (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	category varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	description varchar(5000) NULL,
	price float8 NOT NULL,
	quantity int8 NOT NULL,
	image varchar(1000) NULL,
	CONSTRAINT item_pk PRIMARY KEY (id),
	CONSTRAINT item_quantity_should_be_valid CHECK ((quantity >= 0)),
	CONSTRAINT item_un UNIQUE (uuid)
);

-- user table
CREATE TABLE public."user" (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	first_name varchar(255) NOT NULL,
	last_name varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	"role" varchar(20) NOT NULL,
	status varchar(20) NOT NULL,
	password_hash varchar(255) NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (id),
	CONSTRAINT user_un UNIQUE (uuid),
	CONSTRAINT user_unique_email UNIQUE (email)
);


-- custoemr cart table
CREATE TABLE public.customer_cart (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	customer_id int4 NOT NULL,
	CONSTRAINT customer_cart_pk PRIMARY KEY (id),
	CONSTRAINT customer_cart_un UNIQUE (uuid),
	CONSTRAINT customer_cart_fk FOREIGN KEY (customer_id) REFERENCES public."user"(id)
);

-- cart item table
CREATE TABLE public.cart_item (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	item_id int4 NOT NULL,
	cart_id int4 NOT NULL,
	quantity_in_cart int8 NOT NULL,
	CONSTRAINT cart_item_pk PRIMARY KEY (id),
	CONSTRAINT cart_item_quantity_should_be_valid CHECK ((quantity_in_cart >= 0)),
	CONSTRAINT cart_item_un UNIQUE (uuid),
	CONSTRAINT cart_item_fk FOREIGN KEY (cart_id) REFERENCES public.customer_cart(id),
	CONSTRAINT cart_item_fk_1 FOREIGN KEY (item_id) REFERENCES public.item(id)
);