import React, { FC, useEffect, useState } from 'react';
import styles from './PositionLevelPortfolio.module.css';

import { serverAPI } from '../../../utils/serverAPI';
import { PositionLevelResponse } from '../../../utils/types';

interface PositionLevelPortfolioProps { }

const PositionLevelPortfolio: FC<PositionLevelPortfolioProps> = () => {
  const [data, setData] = useState<PositionLevelResponse[]>([]);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_position_portfolio');
    console.log(result.data);
    setData(result.data);
  }

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  return (
    <div className={styles.PositionLevelPortfolio}>
      <b>Position Level Portfolios</b>
      <div>

        <table>
          <tbody>
            <tr>
              <th>Desk</th>
              <th>Trader</th>
              <th>Book</th>
              <th>Position</th>
              <th>NV</th>
            </tr>
            {data.map((item, index) => {
              return (
                <tr key={index} >
                  <td>{item.desk}</td>
                  <td>{item.trader}</td>
                  <td>{item.book}</td>
                  <td>{item.position}</td>
                  <td>{Number(item.NV).toFixed(2)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>

      </div>
    </div>)
};

export default PositionLevelPortfolio;
