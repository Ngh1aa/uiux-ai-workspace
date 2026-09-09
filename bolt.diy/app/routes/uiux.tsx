import type { MetaFunction } from '@remix-run/cloudflare';
import { ClientOnly } from 'remix-utils/client-only';
import { DesignExperienceV2 } from '~/components/uiux-factory/DesignExperienceV2.client';
import '~/styles/uiux-factory-v2.css';

export const meta: MetaFunction = () => {
  return [
    { title: 'UIUX Factory — Direction Studio' },
    {
      name: 'description',
      content:
        'Direction-first website design workbench powered by Bolt.diy, MetaGPT, real skills_UIUX and web research.',
    },
  ];
};

export default function UIUXFactoryRoute() {
  return (
    <ClientOnly
      fallback={
        <div
          style={{
            minHeight: '100vh',
            display: 'grid',
            placeItems: 'center',
            color: '#8f8a97',
            background: '#0a0a0d',
            fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif',
          }}
        >
          Loading UIUX Factory…
        </div>
      }
    >
      {() => <DesignExperienceV2 />}
    </ClientOnly>
  );
}
