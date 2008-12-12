-- Create table
create table SDW.SERVICE_PROVIDER
(
  ID   NUMBER not null,
  NAME VARCHAR2(50) not null,
  URL  VARCHAR2(200) not null
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
-- Add comments to the columns 
comment on column SERVICE_PROVIDER.ID
  is 'Represents the id of the service provider';
comment on column SERVICE_PROVIDER.NAME
  is 'Represents the name of the service provider';
comment on column SERVICE_PROVIDER.URL
  is 'Represents the url of the service provider';
-- Create/Recreate primary, unique and foreign key constraints 
alter table SDW.SERVICE_PROVIDER
  add constraint PK_SERVICE_PROVIDER primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
