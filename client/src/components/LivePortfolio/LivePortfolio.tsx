import React, { FC, useEffect, useState } from 'react';
import styles from './LivePortfolio.module.css';

import { serverAPI } from '../../utils/serverAPI';
import CashLevelPortFolio from './CashLevelPortfolio/CashLevelPortfolio';
import PositionLevelPortFolio from './PositionLevelPortfolio/PositionLevelPortfolio';
import BondLevelPortfolio from './BondLevelPortfolio/BondLevelPortfolio';
import CurrencyLevelPortfolio from './CurrencyLevelPortfolio/CurrencyLevelPortfolio';

interface LivePortfolioProps {}


const LivePortfolio: FC<LivePortfolioProps> = () => {
  

  return (
    <div className={styles.LivePortfolio}>
      <CashLevelPortFolio />
      <PositionLevelPortFolio />
      <BondLevelPortfolio />
      <CurrencyLevelPortfolio />
    </div>
  );

}

export default LivePortfolio;
