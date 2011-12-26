LP_ADDR_CTRL = 0xB0;
LP_REGS_DBUF = 0x00;
LP_REGS_TPRW = 0x68;

LP_ADDR_SETB = 0x90;
LP_ADDR_QWRT = 0x92;


LP_DBC_ENB = 0x20;
LP_DBC_CPY = 0x10;
LP_DBC_FLS = 0x08;

LP_DBC_B1U = 0x04;
LP_DBC_B0U = 0x00;

LP_DBC_B1D = 0x01;
LP_DBC_B0D = 0x00;


LP_BTN_CLR = 0x08;
LP_BTN_CPY = 0x04;

LP_BTN_GRN1 = 0x20;
LP_BTN_GRN0 = 0x10;

LP_BTN_RED1 = 0x02;
LP_BTN_RED0 = 0x01;

LP_BTN_YLW1 = LP_BTN_GRN1 | LP_BTN_RED1;
LP_BTN_YLW0 = LP_BTN_GRN0 | LP_BTN_RED0;

# shortcuts for high brightness configurations
LP_BTN_YLW = LP_BTN_YLW1 | LP_BTN_YLW0;
LP_BTN_GRN = LP_BTN_GRN1 | LP_BTN_GRN0;
LP_BTN_RED = LP_BTN_RED1 | LP_BTN_RED0;
