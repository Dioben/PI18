BEGIN;
--
-- Create model Simulation
--
CREATE TABLE "simulations" ("id" uuid NOT NULL PRIMARY KEY, "name" varchar(100) NOT NULL, "model" text NOT NULL, "learning_rate" double precision NOT NULL, "isdone" boolean NOT NULL, "isrunning" boolean NOT NULL, "biases" bytea NOT NULL, "layers" integer NOT NULL, "epoch_interval" integer NOT NULL, "goal_epochs" integer NOT NULL, "owner_id" integer NOT NULL);
--
-- Create model Weights
--
CREATE TABLE "weights" ("id" bigserial NOT NULL PRIMARY KEY, "time" timestamp with time zone NOT NULL, "epoch" integer NOT NULL, "layer_index" integer NOT NULL, "layer_name" varchar(150) NOT NULL, "weight" double precision[] NOT NULL, "sim_id" uuid NOT NULL);
DO $do$ BEGIN IF EXISTS ( SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'weights') THEN RAISE EXCEPTION 'assert failed - ''weights'' should not be a hyper table'; ELSE NULL; END IF;END; $do$;
ALTER TABLE "weights" DROP CONSTRAINT "weights_pkey";
SELECT create_hypertable('weights', 'time', chunk_time_interval => interval '1 day', migrate_data => false);
--
-- Create model Update
--
CREATE TABLE "epoch_values" ("id" bigserial NOT NULL PRIMARY KEY, "time" timestamp with time zone NOT NULL, "epoch" integer NOT NULL, "loss" double precision NOT NULL, "accuracy" double precision NOT NULL, "val_loss" double precision NOT NULL, "val_accuracy" double precision NOT NULL, "sim_id" uuid NOT NULL);
DO $do$ BEGIN IF EXISTS ( SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name = 'epoch_values') THEN RAISE EXCEPTION 'assert failed - ''epoch_values'' should not be a hyper table'; ELSE NULL; END IF;END; $do$;
ALTER TABLE "epoch_values" DROP CONSTRAINT "epoch_values_pkey";
SELECT create_hypertable('epoch_values', 'time', chunk_time_interval => interval '1 day', migrate_data => false);
--
-- Create model Tagged
--
CREATE TABLE "Tags" ("id" bigserial NOT NULL PRIMARY KEY, "tag" varchar(200) NOT NULL, "sim_id" uuid NOT NULL, "tagger_id" integer NOT NULL, "iskfold" boolean default FALSE);
--
-- Create index weights_sim_id_5dcd13_idx on field(s) sim, epoch of model weights
--
CREATE INDEX "weights_sim_id_5dcd13_idx" ON "weights" ("sim_id", "epoch");
--
-- Create index weights_sim_id_11ee55_idx on field(s) sim, layer_index of model weights
--
CREATE INDEX "weights_sim_id_11ee55_idx" ON "weights" ("sim_id", "layer_index");
--
-- Create index epoch_value_sim_id_c134a8_idx on field(s) sim, epoch of model update
--
CREATE INDEX "epoch_value_sim_id_c134a8_idx" ON "epoch_values" ("sim_id", "epoch");
--
-- Create index Tags_tag_d28204_idx on field(s) tag of model tagged
--
CREATE INDEX "Tags_tag_d28204_idx" ON "Tags" ("tag");
--
-- Create index Tags_tagger__49a09e_idx on field(s) tagger of model tagged
--
CREATE INDEX "Tags_tagger__49a09e_idx" ON "Tags" ("tagger_id");
--
-- Create index Tags_sim_id_e19bb8_idx on field(s) sim of model tagged
--
CREATE INDEX "Tags_sim_id_e19bb8_idx" ON "Tags" ("sim_id");
--
-- Alter unique_together for tagged (1 constraint(s))
--
ALTER TABLE "Tags" ADD CONSTRAINT "Tags_tag_sim_id_87f794ba_uniq" UNIQUE ("tag", "sim_id");
ALTER TABLE "simulations" ADD CONSTRAINT "simulations_owner_id_8934a030_fk_auth_user_id" FOREIGN KEY ("owner_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "simulations_owner_id_8934a030" ON "simulations" ("owner_id");
ALTER TABLE "weights" ADD CONSTRAINT "weights_sim_id_1d674bea_fk_simulations_id" FOREIGN KEY ("sim_id") REFERENCES "simulations" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "weights_sim_id_1d674bea" ON "weights" ("sim_id");
ALTER TABLE "epoch_values" ADD CONSTRAINT "epoch_values_sim_id_53d5a802_fk_simulations_id" FOREIGN KEY ("sim_id") REFERENCES "simulations" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "epoch_values_sim_id_53d5a802" ON "epoch_values" ("sim_id");
ALTER TABLE "Tags" ADD CONSTRAINT "Tags_sim_id_c60b9dd8_fk_simulations_id" FOREIGN KEY ("sim_id") REFERENCES "simulations" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "Tags" ADD CONSTRAINT "Tags_tagger_id_4870f2e8_fk_auth_user_id" FOREIGN KEY ("tagger_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "Tags_sim_id_c60b9dd8" ON "Tags" ("sim_id");
CREATE INDEX "Tags_tagger_id_4870f2e8" ON "Tags" ("tagger_id");
COMMIT;
