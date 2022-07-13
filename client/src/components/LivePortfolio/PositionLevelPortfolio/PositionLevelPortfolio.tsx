import React, { FC, useEffect, useState } from 'react';
import styles from './PositionLevelPortfolio.module.css';

import { serverAPI } from '../../../utils/serverAPI';

interface PositionLevelPortfolioProps {}
interface TraderModel {
  model: string;
  pk: string;
  fields: {
    desk_id: number;
  }
}

const PositionLevelPortfolio: FC<PositionLevelPortfolioProps> = () => {
  let [data, setData] = useState<TraderModel[]>([]);
  
  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_position_portfolio');
    console.log(result.data);
    setData(result.data);
  }

  
  return (
  <div className={styles.PositionLevelPortfolio}>
  PositionLevelPortfolio Component
  <div>

  <table>
    <tbody>
      <tr>
        <th>Desk</th>
        <th>Trader</th>
      </tr>
      {data.map(item => {
        return (
          <tr key={item.pk} >
            <td>{item.fields.desk_id}</td>
            <td>{item.pk}</td>
          </tr>
        )
      })}
    </tbody>
  </table>

  </div>
  </div>)
};

export default PositionLevelPortfolio;
