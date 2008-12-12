-- Create table
create table SDW.WIDGET_URL_PATTERN
(
  ID        NUMBER not null,
  WIDGET_ID NUMBER not null,
  PATTERN   NVARCHAR2(100) not null
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
-- Create/Recreate primary, unique and foreign key constraints 
alter table SDW.WIDGET_URL_PATTERN
  add constraint PK_WUP primary key (ID)
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
