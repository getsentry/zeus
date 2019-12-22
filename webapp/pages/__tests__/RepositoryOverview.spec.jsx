import xhrmock from 'xhr-mock';
import React from 'react';

import {RepositoryOverview} from '../RepositoryOverview';

describe('RepositoryOverview', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders with all stats', () => {
    let repo = TestStubs.Repository();

    let context = TestStubs.standardContext();
    context.context.repo = repo;

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=builds.duration&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([
          {build: 1770, value: 283000},
          {build: 1769, value: 287000},
          {build: 1768, value: 279000},
          {build: 1767, value: 330000},
          {build: 1766, value: 274000},
          {build: 1764, value: 305000},
          {build: 1763, value: 290000},
          {build: 1762, value: 259000},
          {build: 1761, value: 275000},
          {build: 1760, value: 299000},
          {build: 1759, value: 308000},
          {build: 1755, value: 299000},
          {build: 1753, value: 290000},
          {build: 1751, value: 386000},
          {build: 1750, value: 271000},
          {build: 1749, value: 276000},
          {build: 1748, value: 277000},
          {build: 1747, value: 259000},
          {build: 1746, value: 369000},
          {build: 1745, value: 284000},
          {build: 1722, value: 399000},
          {build: 1721, value: 289000},
          {build: 1716, value: 292000},
          {build: 1713, value: 370000},
          {build: 1712, value: 264000},
          {build: 1711, value: 249000},
          {build: 1703, value: 337000},
          {build: 1699, value: 336000},
          {build: 1698, value: 285000},
          {build: 1697, value: 339000},
          {build: 1696, value: 291000},
          {build: 1695, value: 382000},
          {build: 1694, value: 320000},
          {build: 1692, value: 274000},
          {build: 1684, value: 499000},
          {build: 1676, value: 351000},
          {build: 1660, value: 254000},
          {build: 1654, value: 256000},
          {build: 1627, value: 280000},
          {build: 1626, value: 292000},
          {build: 1625, value: 301000},
          {build: 1621, value: 323000},
          {build: 1617, value: 361000},
          {build: 1611, value: 320000},
          {build: 1607, value: 306000},
          {build: 1606, value: 297000},
          {build: 1605, value: 297000},
          {build: 1599, value: 294000},
          {build: 1592, value: 300000},
          {build: 1588, value: 286000},
          {build: 1583, value: 310000},
          {build: 1577, value: 295000},
          {build: 1553, value: 281000},
          {build: 1549, value: 269000},
          {build: 1548, value: 284000},
          {build: 1545, value: 269000},
          {build: 1544, value: 280000},
          {build: 1543, value: 264000},
          {build: 1542, value: 284000},
          {build: 1541, value: 277000},
          {build: 1537, value: 258000},
          {build: 1535, value: 277000},
          {build: 1530, value: 271000},
          {build: 1529, value: 254000},
          {build: 1528, value: 270000},
          {build: 1527, value: 277000},
          {build: 1523, value: 259000},
          {build: 1522, value: 271000},
          {build: 1521, value: 273000},
          {build: 1520, value: 265000},
          {build: 1519, value: 268000},
          {build: 1518, value: 266000},
          {build: 1517, value: 262000},
          {build: 1516, value: 290000},
          {build: 1515, value: 307000},
          {build: 1514, value: 267000},
          {build: 1513, value: 258000},
          {build: 1512, value: 296000},
          {build: 1511, value: 274000},
          {build: 1510, value: 281000},
          {build: 1507, value: 281000},
          {build: 1451, value: 383000},
          {build: 1441, value: 279000},
          {build: 1436, value: 259000},
          {build: 1434, value: 273000},
          {build: 1433, value: 258000},
          {build: 1432, value: 272000},
          {build: 1431, value: 295000},
          {build: 1429, value: 282000},
          {build: 1423, value: 282000}
        ])
      }
    );

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=coverage.lines_covered&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([
          {build: 1770, value: 8694},
          {build: 1769, value: 8693},
          {build: 1768, value: 8693},
          {build: 1767, value: 8693},
          {build: 1766, value: 8693},
          {build: 1764, value: 8644},
          {build: 1763, value: 8644},
          {build: 1762, value: 8644},
          {build: 1761, value: 8640},
          {build: 1760, value: 8640},
          {build: 1759, value: 8625},
          {build: 1755, value: 8615},
          {build: 1753, value: 8615},
          {build: 1751, value: 8615},
          {build: 1750, value: 8590},
          {build: 1749, value: 8573},
          {build: 1746, value: 8567},
          {build: 1745, value: 8567},
          {build: 1721, value: 8502},
          {build: 1716, value: 8502},
          {build: 1713, value: 8502},
          {build: 1712, value: 8501},
          {build: 1711, value: 8501},
          {build: 1703, value: 8501},
          {build: 1699, value: 8499},
          {build: 1698, value: 8499},
          {build: 1697, value: 8499},
          {build: 1696, value: 8499},
          {build: 1695, value: 8499},
          {build: 1694, value: 8499},
          {build: 1692, value: 8497},
          {build: 1684, value: 8497},
          {build: 1676, value: 8497},
          {build: 1660, value: 8429},
          {build: 1654, value: 8429},
          {build: 1627, value: 8429},
          {build: 1626, value: 8429},
          {build: 1625, value: 8429},
          {build: 1621, value: 8429},
          {build: 1617, value: 8429},
          {build: 1611, value: 8429},
          {build: 1607, value: 8429},
          {build: 1606, value: 8429},
          {build: 1605, value: 8429},
          {build: 1599, value: 8429},
          {build: 1592, value: 8429},
          {build: 1588, value: 8429},
          {build: 1583, value: 8429},
          {build: 1577, value: 8429},
          {build: 1553, value: 8429},
          {build: 1549, value: 8429},
          {build: 1548, value: 8429},
          {build: 1545, value: 8429},
          {build: 1544, value: 8429},
          {build: 1543, value: 8426},
          {build: 1542, value: 8420},
          {build: 1541, value: 8419},
          {build: 1537, value: 8385},
          {build: 1535, value: 8385},
          {build: 1530, value: 8385},
          {build: 1529, value: 8385},
          {build: 1528, value: 8385},
          {build: 1527, value: 8385},
          {build: 1523, value: 8385},
          {build: 1522, value: 8385},
          {build: 1521, value: 8385},
          {build: 1520, value: 8383},
          {build: 1519, value: 8379},
          {build: 1518, value: 8377},
          {build: 1517, value: 8376},
          {build: 1516, value: 8376},
          {build: 1515, value: 8376},
          {build: 1514, value: 8375},
          {build: 1513, value: 8366},
          {build: 1512, value: 8362},
          {build: 1511, value: 8362},
          {build: 1510, value: 8362},
          {build: 1507, value: 8362},
          {build: 1451, value: 8109},
          {build: 1441, value: 8115},
          {build: 1436, value: 8115},
          {build: 1434, value: 8115},
          {build: 1433, value: 8109},
          {build: 1432, value: 8087},
          {build: 1431, value: 8085},
          {build: 1429, value: 8083},
          {build: 1423, value: 8083},
          {build: 1419, value: 8083},
          {build: 1418, value: 8083},
          {build: 1415, value: 8081}
        ])
      }
    );

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=coverage.lines_uncovered&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([
          {build: 1770, value: 2591},
          {build: 1769, value: 2591},
          {build: 1768, value: 2591},
          {build: 1767, value: 2591},
          {build: 1766, value: 2591},
          {build: 1764, value: 2640},
          {build: 1763, value: 2637},
          {build: 1762, value: 2637},
          {build: 1761, value: 2637},
          {build: 1760, value: 2637},
          {build: 1759, value: 2636},
          {build: 1755, value: 2636},
          {build: 1753, value: 2636},
          {build: 1751, value: 2635},
          {build: 1750, value: 2646},
          {build: 1749, value: 2656},
          {build: 1746, value: 2647},
          {build: 1745, value: 2647},
          {build: 1721, value: 2632},
          {build: 1716, value: 2632},
          {build: 1713, value: 2632},
          {build: 1712, value: 2632},
          {build: 1711, value: 2632},
          {build: 1703, value: 2632},
          {build: 1699, value: 2629},
          {build: 1698, value: 2628},
          {build: 1697, value: 2627},
          {build: 1696, value: 2627},
          {build: 1695, value: 2627},
          {build: 1694, value: 2627},
          {build: 1692, value: 2626},
          {build: 1684, value: 2626},
          {build: 1676, value: 2626},
          {build: 1660, value: 3047},
          {build: 1654, value: 3047},
          {build: 1627, value: 3047},
          {build: 1626, value: 3036},
          {build: 1625, value: 3035},
          {build: 1621, value: 3035},
          {build: 1617, value: 3035},
          {build: 1611, value: 3035},
          {build: 1607, value: 3035},
          {build: 1606, value: 3035},
          {build: 1605, value: 3035},
          {build: 1599, value: 3035},
          {build: 1592, value: 3035},
          {build: 1588, value: 3035},
          {build: 1583, value: 3035},
          {build: 1577, value: 3035},
          {build: 1553, value: 3035},
          {build: 1549, value: 3035},
          {build: 1548, value: 3035},
          {build: 1545, value: 3035},
          {build: 1544, value: 3035},
          {build: 1543, value: 3035},
          {build: 1542, value: 3032},
          {build: 1541, value: 3032},
          {build: 1537, value: 2939},
          {build: 1535, value: 2939},
          {build: 1530, value: 2939},
          {build: 1529, value: 2939},
          {build: 1528, value: 2939},
          {build: 1527, value: 2939},
          {build: 1523, value: 2939},
          {build: 1522, value: 2939},
          {build: 1521, value: 2939},
          {build: 1520, value: 2937},
          {build: 1519, value: 2935},
          {build: 1518, value: 2934},
          {build: 1517, value: 2934},
          {build: 1516, value: 2934},
          {build: 1515, value: 2934},
          {build: 1514, value: 2933},
          {build: 1513, value: 2934},
          {build: 1512, value: 2934},
          {build: 1511, value: 2934},
          {build: 1510, value: 2934},
          {build: 1507, value: 2934},
          {build: 1451, value: 2877},
          {build: 1441, value: 2887},
          {build: 1436, value: 2887},
          {build: 1434, value: 2887},
          {build: 1433, value: 2883},
          {build: 1432, value: 2875},
          {build: 1431, value: 2875},
          {build: 1429, value: 2875},
          {build: 1423, value: 2875},
          {build: 1419, value: 2875},
          {build: 1418, value: 2875},
          {build: 1415, value: 2875}
        ])
      }
    );

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=bundle.total_asset_size&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([
          {build: 1770, value: 3023499},
          {build: 1769, value: 3023499},
          {build: 1768, value: 3023499},
          {build: 1767, value: 3023499},
          {build: 1766, value: 3023499},
          {build: 1764, value: 3023499},
          {build: 1763, value: 3023448},
          {build: 1762, value: 3023448},
          {build: 1761, value: 3023448},
          {build: 1760, value: 3023448},
          {build: 1759, value: 3023448},
          {build: 1755, value: 3023448},
          {build: 1753, value: 3023466},
          {build: 1751, value: 3023115},
          {build: 1750, value: 3023180},
          {build: 1749, value: 3023180},
          {build: 1748, value: 3023180},
          {build: 1747, value: 3023180},
          {build: 1746, value: 3023302},
          {build: 1745, value: 3023302},
          {build: 1722, value: 0},
          {build: 1721, value: 3023380},
          {build: 1716, value: 3023375},
          {build: 1713, value: 3023365},
          {build: 1712, value: 3012015},
          {build: 1711, value: 0},
          {build: 1703, value: 3012015},
          {build: 1699, value: 3011728},
          {build: 1698, value: 3011632},
          {build: 1697, value: 0},
          {build: 1696, value: 3011488},
          {build: 1695, value: 3011487},
          {build: 1694, value: 2988371},
          {build: 1692, value: 0},
          {build: 1684, value: 2988453},
          {build: 1676, value: 2988574},
          {build: 1660, value: 1973823},
          {build: 1654, value: 0},
          {build: 1627, value: 1973823},
          {build: 1626, value: 1973311},
          {build: 1625, value: 0},
          {build: 1621, value: 0},
          {build: 1617, value: 1950427},
          {build: 1611, value: 1950427},
          {build: 1607, value: 1950427},
          {build: 1606, value: 1950427},
          {build: 1605, value: 1950427},
          {build: 1599, value: 1948755},
          {build: 1592, value: 1948755},
          {build: 1588, value: 1948755},
          {build: 1583, value: 1948755},
          {build: 1577, value: 1948755},
          {build: 1553, value: 1948755},
          {build: 1549, value: 1948755},
          {build: 1548, value: 1948755},
          {build: 1545, value: 1948755},
          {build: 1544, value: 0},
          {build: 1543, value: 1948755},
          {build: 1542, value: 1948755},
          {build: 1541, value: 1948755},
          {build: 1537, value: 1948124},
          {build: 1535, value: 0},
          {build: 1530, value: 0},
          {build: 1529, value: 0},
          {build: 1528, value: 0},
          {build: 1527, value: 0},
          {build: 1523, value: 0},
          {build: 1522, value: 1948090},
          {build: 1521, value: 1948090},
          {build: 1520, value: 1948090},
          {build: 1519, value: 1948090},
          {build: 1518, value: 1948090},
          {build: 1517, value: 1948090},
          {build: 1516, value: 1948042},
          {build: 1515, value: 1948008},
          {build: 1514, value: 1948008},
          {build: 1513, value: 1948008},
          {build: 1512, value: 1948008},
          {build: 1511, value: 1948008},
          {build: 1510, value: 1948008},
          {build: 1507, value: 1948008},
          {build: 1451, value: 1942593},
          {build: 1441, value: 1942593},
          {build: 1436, value: 1942593},
          {build: 1434, value: 1942593},
          {build: 1433, value: 1942593},
          {build: 1432, value: 1942593},
          {build: 1431, value: 1942593},
          {build: 1429, value: 1942593},
          {build: 1423, value: 1942593}
        ])
      }
    );

    const wrapper = TestStubs.mount(
      <RepositoryOverview
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name
        }}
        revisionList={[TestStubs.Revision()]}
      />,
      context
    );
    expect(wrapper).toMatchSnapshot();
  });

  it('hides empty stats', () => {
    let repo = TestStubs.Repository();

    let context = TestStubs.standardContext();
    context.context.repo = repo;

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=builds.duration&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=coverage.lines_covered&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=coverage.lines_uncovered&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );

    xhrmock.get(
      `/api/repos/${repo.full_name}/stats?stat=bundle.total_asset_size&resolution=1d&points=90&aggregate=build`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );

    const wrapper = TestStubs.mount(
      <RepositoryOverview
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name
        }}
        revisionList={[TestStubs.Revision()]}
      />,
      context
    );
    expect(wrapper).toMatchSnapshot();
  });
});
