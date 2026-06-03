export type Screenshot = {
  id: string;
  filename: string;
  url: string;
  source: 'web' | 'app' | 'android';
  label: string;
};
