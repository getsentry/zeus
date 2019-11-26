import {getDuration} from '../duration';

describe('getDuration', () => {
  it('handles weeks', () => {
    expect(getDuration(604800090)).toBe('1 week');
    expect(getDuration(604800090, true)).toBe('1w');
    expect(getDuration(1204800090)).toBe('2 weeks');
    expect(getDuration(1204800090, true)).toBe('2w');
  });

  it('handles days', () => {
    expect(getDuration(172800000)).toBe('2 days');
    expect(getDuration(172800000, true)).toBe('2d');
  });

  it('handles hours', () => {
    expect(getDuration(7200000)).toBe('2 hours');
    expect(getDuration(7200000, true)).toBe('2h');
  });

  it('handles minutes', () => {
    expect(getDuration(120000)).toBe('2 minutes');
    expect(getDuration(120000, true)).toBe('2m');
  });

  it('handles seconds', () => {
    expect(getDuration(1000)).toBe('1 second');
    expect(getDuration(1000, true)).toBe('1s');
    expect(getDuration(2000)).toBe('2 seconds');
    expect(getDuration(2000, true)).toBe('2s');
  });

  it('handles milliseconds', () => {
    expect(getDuration(50)).toBe('0.05 seconds');
    expect(getDuration(50, true)).toBe('0.05s');
  });
});
