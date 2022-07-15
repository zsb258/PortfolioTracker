import React, { FC, useState, useEffect } from 'react';
import styles from './Header.module.css';

import { serverAPI } from '../../utils/serverAPI';

interface HeaderProps {}

const Header: FC<HeaderProps> = () => {
  const [data, setData] = useState<number>(-1);

  const fetchData = async () => {
    const result = await serverAPI.get('api/get_latest_event_id');
    console.log(result.data);
    setData(result.data);
  };
  useEffect(() => {
    fetchData();  // fetch data on component mount
  }, []);

  useEffect(() => {
    fetchData();
    const handleScheduledFetching = setInterval(() => {
      fetchData();
    }, 5_000);  // every 5 seconds

    return () => clearInterval(handleScheduledFetching);
  }, []);

  const [waitingBar, setWaitingBar] = useState<number>(5);

  useEffect(() => {
    if (waitingBar === 0){
      setWaitingBar(5);
    }
    const intervalId = setInterval(() => {
      setWaitingBar(waitingBar - 1);
    }, 1000);
    return () => clearInterval(intervalId);
  }, [waitingBar]);

  return (
    <div className={styles.Header}>
      Latest event ID: {data}
      <div>
        Fetching updates in {waitingBar}...
      </div>
    </div>
  );
};

export default Header;
