export const getSize = value => {
  if (value === 0) return '0 B';
  if (!value) return null;

  let i = Math.floor(Math.log(value) / Math.log(1024));
  return (
    (value / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i]
  );
};
