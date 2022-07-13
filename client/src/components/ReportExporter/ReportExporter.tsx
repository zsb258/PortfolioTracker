import React, { FC, useState, useEffect } from 'react';
import styles from './ReportExporter.module.css';

import { serverAPI } from '../../utils/serverAPI';

interface ReportExporterProps {}

const ReportExporter: FC<ReportExporterProps> = () => {

  return (
  <div className={styles.ReportExporter}>
    ReportExporter Component
    <div>To implement</div>
  </div>
  )
};

export default ReportExporter;
