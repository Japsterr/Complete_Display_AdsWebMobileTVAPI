import React, { useEffect, useState } from 'react';
import { Box, Button, Heading, SimpleGrid, Text } from '@chakra-ui/react';
import { fetchMenus, deleteMenu } from '../services/api';

export default function MenuManagementPage(){
  const [menus, setMenus] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try{
      const data = await fetchMenus();
      setMenus(data);
    }catch(e){
      console.error(e);
    }finally{ setLoading(false); }
  };

  useEffect(()=>{ load(); }, []);

  return (
    <Box p={6}>
      <Heading mb={4}>Menu Management</Heading>
      <Button colorScheme="green" mb={4} onClick={() => window.location.href = '/menus/new'}>Create menu</Button>
      {loading && <Text>Loading...</Text>}
      <SimpleGrid columns={3} spacing={4}>
        {menus.map(m => (
          <Box key={m.menu_id} borderWidth={1} p={4} borderRadius={6}>
            <Heading size="md">{m.name}</Heading>
            <Text>Items: {m.items?.length || 0}</Text>
            <Button size="sm" mt={2} onClick={() => window.location.href = `/menus/${m.menu_id}/edit`} mr={2}>Edit</Button>
            <Button size="sm" mt={2} colorScheme="red" onClick={async ()=>{ await deleteMenu(m.menu_id); load(); }}>Delete</Button>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
}
