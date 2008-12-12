-- Create table
create table SDW.WIDGET
(
  ID                  NUMBER not null,
  SERVICE_PROVIDER_ID NUMBER not null,
  NAME                VARCHAR2(50) not null
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
comment on column WIDGET.ID
  is 'ID is the primary key';
comment on column WIDGET.SERVICE_PROVIDER_ID
  is 'SERVICE_ID is the foreign key';
comment on column WIDGET.NAME
  is 'Represents the name of the widget';
-- Create/Recreate primary, unique and foreign key constraints 
alter table SDW.WIDGET
  add constraint PK_WIDGET primary key (ID)
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
