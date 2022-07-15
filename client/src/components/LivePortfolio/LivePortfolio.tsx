import React, { FC, useEffect, useState } from 'react';
import styles from './LivePortfolio.module.css';
import { styled } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';

import PositionLevelPortFolio from './PositionLevelPortfolio/PositionLevelPortfolio';
import BondLevelPortfolio from './BondLevelPortfolio/BondLevelPortfolio';
import CurrencyLevelPortfolio from './CurrencyLevelPortfolio/CurrencyLevelPortfolio';
import Exclusions from './Exclusions/Exclusions';

interface LivePortfolioProps {}


const LivePortfolio: FC<LivePortfolioProps> = () => {
  

  return (
    <div className={styles.LivePortfolio}>
      <Box sx={{ width: '100%' }}>
      <Grid container rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
        <Grid item xs={6}>
          <PositionLevelPortFolio />
        </Grid>
        <Grid item xs={6}>
          <BondLevelPortfolio />
        </Grid>
        <Grid item xs={6}>
          <CurrencyLevelPortfolio />
        </Grid>
        <Grid item xs={6}>
          <Exclusions />
        </Grid>
      </Grid>
    </Box>
    </div>
  );

}

export default LivePortfolio;
