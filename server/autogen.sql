BEGIN;
--
-- Create model Simulation
--
CREATE TABLE "Simulations" ("time" timestamp with time zone NOT NULL, "id" uuid NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL, "model" text NOT NULL, "isdone" boolean NOT NULL, "isrunning" boolean NOT NULL, "biases" bytea NOT NULL, "epoch_interval" integer NOT NULL, "goal_epochs" integer NOT NULL, "owner_id" integer NOT NULL);
DO $do$ BEGIN IF EXISTS ( SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'Simulations') THEN RAISE EXCEPTION 'assert failed - ''Simulations'' should not be a hyper table'; ELSE NULL; END IF;END; $do$;
ALTER TABLE "Simulations" DROP CONSTRAINT "Simulations_pkey";
SELECT create_hypertable('Simulations', 'time', chunk_time_interval => interval '1 day', migrate_data => false);
--
-- Create model Weights
--
CREATE TABLE "Weights" ("id" bigserial NOT NULL PRIMARY KEY, "time" timestamp with time zone NOT NULL, "epoch" integer NOT NULL, "layer" integer NOT NULL, "weight" bytea NOT NULL, "sim_id" uuid NOT NULL);
DO $do$ BEGIN IF EXISTS ( SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'Weights') THEN RAISE EXCEPTION 'assert failed - ''Weights'' should not be a hyper table'; ELSE NULL; END IF;END; $do$;
ALTER TABLE "Weights" DROP CONSTRAINT "Weights_pkey";
SELECT create_hypertable('Weights', 'time', chunk_time_interval => interval '1 day', migrate_data => false);
--
-- Create model Update
--
CREATE TABLE "Updates" ("id" bigserial NOT NULL PRIMARY KEY, "time" timestamp with time zone NOT NULL, "epoch" integer NOT NULL, "loss" double precision NOT NULL, "accuracy" double precision NOT NULL, "sim_id" uuid NOT NULL);
DO $do$ BEGIN IF EXISTS ( SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'Updates') THEN RAISE EXCEPTION 'assert failed - ''Updates'' should not be a hyper table'; ELSE NULL; END IF;END; $do$;
ALTER TABLE "Updates" DROP CONSTRAINT "Updates_pkey";
SELECT create_hypertable('Updates', 'time', chunk_time_interval => interval '1 day', migrate_data => false);
--
-- Create model Tagged
--
CREATE TABLE "Tags" ("id" bigserial NOT NULL PRIMARY KEY, "tag" varchar(200) NOT NULL, "sim_id" uuid NOT NULL);
ALTER TABLE "Simulations" ADD CONSTRAINT "Simulations_owner_id_0c2cd571_fk_auth_user_id" FOREIGN KEY ("owner_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "Simulations_owner_id_0c2cd571" ON "Simulations" ("owner_id");
ALTER TABLE "Weights" ADD CONSTRAINT "Weights_sim_id_a9a5120a_fk_Simulations_id" FOREIGN KEY ("sim_id") REFERENCES "Simulations" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "Weights_sim_id_a9a5120a" ON "Weights" ("sim_id");
ALTER TABLE "Updates" ADD CONSTRAINT "Updates_sim_id_2568308b_fk_Simulations_id" FOREIGN KEY ("sim_id") REFERENCES "Simulations" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "Updates_sim_id_2568308b" ON "Updates" ("sim_id");
ALTER TABLE "Tags" ADD CONSTRAINT "Tags_tag_sim_id_87f794ba_uniq" UNIQUE ("tag", "sim_id");
ALTER TABLE "Tags" ADD CONSTRAINT "Tags_sim_id_c60b9dd8_fk_Simulations_id" FOREIGN KEY ("sim_id") REFERENCES "Simulations" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "Tags_sim_id_c60b9dd8" ON "Tags" ("sim_id");
COMMIT;
